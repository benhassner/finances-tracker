import { Link, useLocation } from 'react-router-dom'

const Navigation = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/transactions', label: 'Transactions' },
    { path: '/income', label: 'Income' },
    { path: '/import', label: 'Import' },
    { path: '/rules', label: 'Rules' },
    { path: '/categories', label: 'Categories' },
    { path: '/alerts', label: 'Alerts' },
  ]

  return (
    <nav className="bg-finance-bg border-b border-gray-700/50 backdrop-blur-md sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <h1 className="text-2xl font-display font-bold text-finance-accent hover:text-finance-highlight transition-colors duration-200">
              💰 Finance Tracker
            </h1>
            <div className="hidden md:flex space-x-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                    location.pathname === item.path
                      ? 'bg-finance-accent text-finance-bg shadow-lg shadow-finance-accent/30'
                      : 'text-finance-text-secondary hover:text-finance-text-primary hover:bg-finance-card'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navigation