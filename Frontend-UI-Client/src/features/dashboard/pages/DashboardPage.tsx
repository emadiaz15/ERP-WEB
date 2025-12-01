/**
 * DashboardPage
 * Página principal del dashboard
 */

import { Card, CardHeader, CardBody, Badge } from '@/shared/ui'

export function DashboardPage() {
  const stats = [
    {
      name: 'Ventas del Mes',
      value: '$45,231.89',
      change: '+20.1%',
      trend: 'up' as const,
    },
    {
      name: 'Productos en Stock',
      value: '2,543',
      change: '+180',
      trend: 'up' as const,
    },
    {
      name: 'Órdenes Pendientes',
      value: '89',
      change: '-12',
      trend: 'down' as const,
    },
    {
      name: 'Clientes Activos',
      value: '573',
      change: '+48',
      trend: 'up' as const,
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Resumen general del sistema ERP
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.name} padding="md">
            <div>
              <p className="text-sm font-medium text-gray-600">{stat.name}</p>
              <div className="mt-2 flex items-baseline justify-between">
                <p className="text-2xl font-semibold text-gray-900">
                  {stat.value}
                </p>
                <Badge
                  variant={stat.trend === 'up' ? 'success' : 'error'}
                  size="sm"
                >
                  {stat.change}
                </Badge>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader
          title="Actividad Reciente"
          subtitle="Últimas transacciones y eventos del sistema"
        />
        <CardBody>
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className="flex items-center justify-between border-b border-gray-100 pb-4 last:border-0 last:pb-0"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-50">
                    <svg
                      className="h-5 w-5 text-brand-500"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                      />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      Nueva venta registrada
                    </p>
                    <p className="text-sm text-gray-500">
                      Hace {i} hora{i > 1 ? 's' : ''}
                    </p>
                  </div>
                </div>
                <Badge variant="success">Completada</Badge>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

export default DashboardPage
