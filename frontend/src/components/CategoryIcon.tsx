import React from 'react'

interface CategoryIconProps {
  category: string
  className?: string
}

const CategoryIcon: React.FC<CategoryIconProps> = ({ category, className = 'w-6 h-6' }) => {
  const keyFrom = (raw: string) => {
    const c = raw.toLowerCase()
    const has = (s: string) => c.includes(s)
    if (has('grocery') || has('supermarket')) return 'groceries'
    if (has('dining') || has('restaurant') || has('food') || has('eat')) return 'dining out'
    if (has('gas') || has('fuel')) return 'gas & fuel'
    if (has('subscription') || has('recurring')) return 'subscriptions'
    if (has('rent') || has('housing') || has('mortgage') || has('home')) return 'rent & housing'
    if (has('income') || has('salary') || has('paycheck') || has('wage')) return 'income'
    if (has('util') || has('electric') || has('water') || has('internet') || has('phone') || has('wifi')) return 'utilities'
    if (has('health') || has('medical') || has('doctor') || has('pharm')) return 'healthcare'
    if (has('entertain') || has('movie') || has('music') || has('game')) return 'entertainment'
    if (has('shop') || has('retail') || has('store')) return 'shopping'
    if (has('travel') || has('flight') || has('hotel') || has('air')) return 'travel'
    if (has('insur')) return 'insurance'
    if (has('educat') || has('school') || has('tuition')) return 'education'
    if (has('personal') || has('care') || has('beauty') || has('groom')) return 'personal care'
    if (has('transfer') || has('zelle') || has('venmo')) return 'transfers'
    return c
  }

  const key = keyFrom(category)

  switch (key) {
    case 'groceries':
      // Shopping cart
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="9" cy="20" r="1.5" />
          <circle cx="17" cy="20" r="1.5" />
          <path d="M3 4h2l2 12h10l2-8H6" />
          <path d="M7 4h4l2 4H9z" />
        </svg>
      )
    case 'dining out':
      // Fork and knife
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="6" y1="3" x2="6" y2="12" />
          <line x1="10" y1="3" x2="10" y2="12" />
          <line x1="8" y1="3" x2="8" y2="12" />
          <line x1="8" y1="12" x2="8" y2="21" />
          <path d="M16 3v7a2 2 0 0 1-2 2h0v9" />
        </svg>
      )
    case 'gas & fuel':
      // Gas pump
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="4" y="6" width="10" height="14" rx="2" />
          <line x1="8" y1="10" x2="10" y2="10" />
          <path d="M14 7h2l3 3v7a2 2 0 0 1-2 2h-1" />
          <path d="M19 10h2l1 1" />
        </svg>
      )
    case 'subscriptions':
      // Repeat arrows around dollar
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 12a8 8 0 0 1 13.66-5.66" />
          <polyline points="18 3 17 6 14 5" />
          <path d="M20 12a8 8 0 0 1-13.66 5.66" />
          <polyline points="6 21 7 18 10 19" />
          <path d="M12 8c-1.5 0-2.5.7-2.5 1.75S11 12 12.5 12s2.5.7 2.5 1.75S13.5 15.5 12 15.5" />
          <line x1="12" y1="6.5" x2="12" y2="8" />
          <line x1="12" y1="15.5" x2="12" y2="17" />
        </svg>
      )
    case 'rent & housing':
      // House
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="3 10 12 3 21 10" />
          <rect x="5" y="10" width="14" height="10" rx="2" />
          <line x1="12" y1="10" x2="12" y2="20" />
        </svg>
      )
    case 'income':
      // Arrow trending up
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="4 14 9 9 13 13 20 6" />
          <polyline points="20 10 20 6 16 6" />
        </svg>
      )
    case 'utilities':
      // Lightning bolt
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="13 2 3 14 10 14 8 22 18 10 11 10" />
        </svg>
      )
    case 'healthcare':
      // Medical cross
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="4" y="4" width="16" height="16" rx="3" />
          <line x1="12" y1="7" x2="12" y2="17" />
          <line x1="7" y1="12" x2="17" y2="12" />
        </svg>
      )
    case 'entertainment':
      // Play button in circle
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="9" />
          <polygon points="10 8 16 12 10 16 10 8" />
        </svg>
      )
    case 'shopping':
      // Shopping bag
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M6 8h12l-1 12H7L6 8z" />
          <path d="M9 8a3 3 0 0 1 6 0" />
        </svg>
      )
    case 'travel':
      // Airplane / paper plane
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="3 12 21 3 14 21 12 13 3 12" />
        </svg>
      )
    case 'insurance':
      // Shield
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2l7 3v6c0 5-3.5 9-7 11-3.5-2-7-6-7-11V5l7-3z" />
        </svg>
      )
    case 'education':
      // Graduation cap
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="12 5 3 10 12 15 21 10 12 5" />
          <path d="M7 12v3c0 1.66 2.69 3 5 3s5-1.34 5-3v-3" />
          <line x1="21" y1="10" x2="21" y2="15" />
        </svg>
      )
    case 'personal care':
      // Clean symmetric heart
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 20.5s-6.5-4.1-8.5-7C2 11 3.6 7.5 7 7.5c1.7 0 3 .9 5 2.6 2-1.7 3.3-2.6 5-2.6 3.4 0 5 3.5 3.5 6-2 2.9-8.5 7-8.5 7z" />
        </svg>
      )
    case 'transfers':
      // Left-right arrows
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="7 7 3 11 7 15" />
          <line x1="3" y1="11" x2="15" y2="11" />
          <polyline points="17 9 21 13 17 17" />
          <line x1="9" y1="13" x2="21" y2="13" />
        </svg>
      )
    default:
      // Question mark for other/unknown
      return (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="9" />
          <path d="M9.5 9a2.5 2.5 0 0 1 5 0c0 2-2.5 2-2.5 4" />
          <circle cx="12" cy="17" r="1" />
        </svg>
      )
  }
}

export default CategoryIcon
