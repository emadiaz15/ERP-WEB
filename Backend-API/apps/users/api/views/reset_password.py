from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError

from apps.users.docs.user_doc import password_reset_confirm_doc
from apps.users.api.repositories.user_repository import UserRepository
from apps.users.api.serializers.password_reset_serializers import PasswordResetConfirmSerializer
from apps.users.models.user_model import User


@api_view(['POST'])
@permission_classes([IsAdminUser])
@extend_schema(**password_reset_confirm_doc)
def password_reset_confirm(request, uidb64: str, token: str):
    """
    🛠️ Permite a un administrador restablecer la contraseña de un usuario mediante token y uid.
    🔐 Seguridad: solo admins pueden usar este endpoint.
    """
    # Solo permiten cambiar password usuarios con rol ADMIN o MANAGER
    current_user: User = request.user
    if current_user.role not in [User.Role.ADMIN, User.Role.MANAGER]:
        return Response(
            {'detail': 'Solo usuarios con rol ADMIN o MANAGER pueden restablecer contraseñas.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    new_password = serializer.validated_data["password"]

    try:
        user = UserRepository.confirm_password_reset(uidb64, token, new_password)
        # Invalida caché explícitamente para el usuario afectado
        from apps.users.utils.cache_invalidation import invalidate_user_cache
        invalidate_user_cache(user_id=user.id)
        return Response(
            {'message': 'Contraseña restablecida correctamente.'},
            headers={"X-Invalidate-Users-Cache": "true"},
            status=status.HTTP_200_OK
        )
    except ValidationError as e:
        detail = str(e.detail) if hasattr(e, 'detail') else str(e)
        return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(
            {'detail': f'Error interno al restablecer la contraseña: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
