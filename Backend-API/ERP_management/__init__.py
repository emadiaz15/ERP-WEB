from .celery import app as celery_app

__all__ = ("celery_app",)

# Soporte opcional para PyMySQL como reemplazo de MySQLdb
try:
	import pymysql  # type: ignore
	pymysql.install_as_MySQLdb()
except Exception:
	# Si no está instalado, no es crítico a menos que habilites MYSQL_RO
	pass
