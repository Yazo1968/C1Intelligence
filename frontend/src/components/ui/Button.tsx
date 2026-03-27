interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md';
}

const variants = {
  primary: 'bg-navy-900 text-white hover:bg-navy-800 disabled:bg-navy-700 disabled:opacity-50',
  secondary: 'bg-white text-navy-900 border border-gray-300 hover:bg-gray-50 disabled:opacity-50',
  danger: 'bg-red-600 text-white hover:bg-red-700 disabled:opacity-50',
};

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
};

export function Button({ variant = 'primary', size = 'md', className = '', children, ...props }: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center font-medium rounded-md transition-colors cursor-pointer ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
