from apps.users.utils.cache_decorators import list_cache, detail_cache
from apps.users.utils.cache_invalidation import invalidate_user_cache
from apps.core.utils import broadcast_crud_event
import logging
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_spectacular.utils import extend_schema
from django.db.models import Q, Value
from django.db.models.functions import Lower
from django.db import connection
import unicodedata

from apps.users.models.user_model import User
from apps.users.api.repositories.user_repository import UserRepository
from apps.users.api.serializers.user_create_serializers import UserCreateSerializer
from apps.users.api.serializers.user_update_serializers import UserUpdateSerializer
from apps.users.api.serializers.user_detail_serializers import UserDetailSerializer
from apps.storages_client.services.profile_image import (
    delete_profile_image,
    replace_profile_image,
)
from apps.core.pagination import Pagination
from ...filters import UserFilter
from apps.users.docs.user_doc import (
    get_user_profile_doc, list_users_doc, create_user_doc,
    manage_user_doc, image_delete_doc, image_replace_doc, user_lookup_doc
)

logger = logging.getLogger(__name__)

@extend_schema(**get_user_profile_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    serializer = UserDetailSerializer(
        request.user,
        context={"request": request, "include_image_url": True}
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(**user_lookup_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_lookup_view(request):
    """Búsqueda liviana para n8n: ?q=Nombre Apellido (case/acento insensitive).
    Devuelve id, full_name. Si no hay resultados indicarlo.
    Intentamos usar unaccent si está disponible, si no, hacemos normalización básica.
    """
    q = (request.GET.get('q') or '').strip()
    if not q:
        return Response({'results': [], 'detail': 'Parámetro q vacío.'}, status=200)

    def strip_accents(s: str) -> str:
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

    original_q = q
    q_norm = strip_accents(q.lower())
    terms = [t for t in re_split_safe(q_norm) if t]
    qs = User.objects.filter(is_active=True).annotate(_name_norm=Lower('name'), _last_norm=Lower('last_name'))

    # Detectar disponibilidad de unaccent (Postgres) – simple prueba.
    unaccent_available = False
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_available_extensions WHERE name='unaccent';")
            res = cur.fetchall()
            if res:
                unaccent_available = True
    except Exception:
        unaccent_available = False

    # Construir filtro incremental
    filters = Q()
    for term in terms:
        if unaccent_available:
            # Intentar usar función unaccent vía extra. (Depende de PG)
            filters &= (
                Q(name__unaccent__icontains=term) |
                Q(last_name__unaccent__icontains=term)
            )
        else:
            # Fallback: comparar contra versión normalizada a mano
            filters &= (
                Q(_name_norm__icontains=term) |
                Q(_last_norm__icontains=term)
            )

    qs = qs.filter(filters)[:25]
    results = []
    for u in qs:
        full_name = f"{u.name} {u.last_name}".strip()
        fn_norm = strip_accents(full_name.lower())
        # simple prioridad: términos todos presentes
        if all(t in fn_norm for t in terms):
            results.append({'id': u.id, 'full_name': full_name})
    if not results:
        return Response({'results': [], 'detail': 'No se encontraron usuarios para la consulta.'}, status=200)
    return Response({'results': results})


def re_split_safe(q: str):
    try:
        import re as _re
        return _re.split(r"\s+", q)
    except Exception:
        return [q]


@extend_schema(**list_users_doc)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
@list_cache
def user_list_view(request):
    queryset = UserRepository.get_all_active_users().order_by('-created_at')
    filterset = UserFilter(request.GET, queryset=queryset)
    if not filterset.is_valid():
        return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

    paginator = Pagination()
    page = paginator.paginate_queryset(filterset.qs, request)
    serializer = UserDetailSerializer(
        page,
        many=True,
        context={"request": request, "include_image_url": True}
    )
    return paginator.get_paginated_response(serializer.data)


@extend_schema(**create_user_doc)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
@parser_classes([MultiPartParser])
def user_create_view(request):
    serializer = UserCreateSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        user = serializer.save()
        response_data = UserDetailSerializer(
            user,
            context={"request": request, "include_image_url": True}
        ).data
        # Invalida caché y emite evento WebSocket
        invalidate_user_cache(user.id)
        broadcast_crud_event(
            event_type="create",
            app="users",
            model="User",
            data=response_data
        )
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(**manage_user_doc)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def user_detail_view(request, pk=None):
    user_instance = UserRepository.get_by_id(pk)
    if not user_instance:
        return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    is_self = request.user.id == user_instance.id
    is_admin = request.user.is_staff

    if request.method == 'GET':
        if not (is_admin or is_self):
            return Response({'detail': 'No tienes permiso para ver este perfil.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserDetailSerializer(
            user_instance,
            context={"request": request, "include_image_url": True}
        )
        return Response(serializer.data)

    if request.method == 'PUT':
        if not (is_admin or is_self):
            return Response({'detail': 'No tienes permiso para actualizar este usuario.'}, status=status.HTTP_403_FORBIDDEN)

        if not is_admin:
            allowed_fields = {'name', 'last_name', 'dni', 'email', 'image', 'phone'}
            for field in request.data:
                if field not in allowed_fields:
                    return Response({'detail': f'No puedes modificar el campo "{field}".'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserUpdateSerializer(
            user_instance,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        if serializer.is_valid():
            updated_user = serializer.save()
            response_data = UserDetailSerializer(
                updated_user,
                context={"request": request, "include_image_url": True}
            ).data
            # Invalida caché y emite evento WebSocket
            invalidate_user_cache(updated_user.id)
            broadcast_crud_event(
                event_type="update",
                app="users",
                model="User",
                data=response_data
            )
            return Response(response_data, headers={"X-Invalidate-Users-Cache": "true"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if not is_admin:
            return Response({'detail': 'No tienes permiso para eliminar este usuario.'}, status=status.HTTP_403_FORBIDDEN)

        if user_instance.image:
            try:
                delete_profile_image(user_instance.image, user_instance.id)
                user_instance.image = None
                user_instance.save(update_fields=["image"])
            except Exception as e:
                logger.warning(f"⚠️ Error al eliminar imagen de perfil: {e}")

        UserRepository.soft_delete(user_instance)
        # Invalida caché y emite evento WebSocket
        invalidate_user_cache(user_instance.id)
        broadcast_crud_event(
            event_type="delete",
            app="users",
            model="User",
            data={"id": user_instance.id}
        )
        return Response(
            {'message': 'Usuario eliminado (soft) correctamente y su imagen también.'},
            headers={"X-Invalidate-Users-Cache": "true"}
        )


@extend_schema(**image_replace_doc)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def image_replace_view(request, file_id: str):
    target_user = request.user
    if request.user.is_staff:
        user_id_param = request.GET.get("user_id")
        if not user_id_param:
            return Response({"detail": "Falta el parámetro user_id."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            target_user = User.objects.get(id=user_id_param)
        except User.DoesNotExist:
            return Response({"detail": "Usuario destino no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if not file_id or not target_user.image:
        return Response({"detail": "No hay imagen para reemplazar."}, status=status.HTTP_400_BAD_REQUEST)

    if str(target_user.image) != str(file_id):
        return Response({"detail": "El ID de imagen no coincide con el usuario."}, status=status.HTTP_403_FORBIDDEN)

    new_file = request.FILES.get("file")
    if not new_file:
        return Response({"detail": "Archivo requerido."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = replace_profile_image(new_file, file_id, target_user.id)
        target_user.image = result.get("key")
        target_user.save(update_fields=["image"])
        # devolver la URL actualizada
        data = UserDetailSerializer(
            target_user,
            context={"request": request, "include_image_url": True}
        ).data
        return Response(data, headers={"X-Invalidate-Users-Cache": "true"})
    except Exception as e:
        logger.warning(f"Error al reemplazar imagen: {e}")
        return Response({"detail": "Error al reemplazar imagen."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(**image_delete_doc)
@api_view(["DELETE", "POST"])
@permission_classes([IsAuthenticated])
def image_delete_view(request, file_id: str = None):
    # Depuración extendida: imprimimos método, headers y cuerpo para entender por qué
    # el parámetro `user_id` podría no llegar desde el frontend.
    print("[DEBUG] Entrando a image_delete_view")
    try:
        content_type = request.META.get('CONTENT_TYPE')
    except Exception:
        content_type = None
    try:
        raw_body = request.body.decode('utf-8') if request.body else ''
    except Exception:
        raw_body = '<no-decodable-body>'
    print(f"[DEBUG] method={request.method} CONTENT_TYPE={content_type}")
    print(f"[DEBUG] query_params={request.query_params}")
    print(f"[DEBUG] data={request.data}")
    print(f"[DEBUG] raw_body={raw_body}")
    requester = request.user
    user_id = request.query_params.get("user_id") or request.data.get("user_id")

    # Solo admin puede borrar imagen de otro usuario
    if requester.is_staff and user_id:
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Usuario objetivo no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    else:
        user = requester

    # Soportar file_id vía path o file_path vía query param o body
    file_path = request.query_params.get("file_path") or request.data.get("file_path")
    if not file_id and not file_path:
        return Response({"detail": "Falta el ID de la imagen."}, status=status.HTTP_400_BAD_REQUEST)

    effective_file_id = file_id if file_id else file_path
    print(f"[DEBUG] Comparando: user.id={user.id} user.image={user.image!r} vs effective_file_id={effective_file_id!r}")

    if not user.image:
        return Response({"detail": "El usuario no tiene imagen asociada."}, status=status.HTTP_400_BAD_REQUEST)

    # Solo permitir si la imagen corresponde al usuario objetivo
    if str(user.image) != str(effective_file_id):
        return Response({"detail": "No tienes permiso para eliminar esta imagen."}, status=status.HTTP_403_FORBIDDEN)

    try:
        delete_profile_image(effective_file_id, user.id)
    except Exception as e:
        logger.warning(f"Error al eliminar imagen: {e}")
        return Response({"detail": "Error al eliminar imagen."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    user.image = ""
    user.save(update_fields=["image"])
    # devolvemos la nueva representación sin imagen
    data = UserDetailSerializer(
        user,
        context={"request": request, "include_image_url": True}
    ).data
    return Response(data, headers={"X-Invalidate-Users-Cache": "true"})
