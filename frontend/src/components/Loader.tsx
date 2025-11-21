import tridentImage from '@/assets/trident.png';

/**
 * Загальний Loader з тризубом України
 * 
 * Щоб використати PNG:
 * 1. Поклади trident.png в: frontend/src/assets/trident.png
 * 2. Розкоментуй імпорт вгорі
 * 3. Розкоментуй <img> нижче і закоментуй <svg>
 */
export function Loader() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 -mt-20">
      <div className="animate-pulse">
          <img src={tridentImage} alt="Trident" className="w-16 h-16" />
      </div>
    </div>
  );
}

export function MiniLoader({ size = 40 }: { size?: number }) {
  return (
    <div className="flex items-center justify-center">
      <svg
        width={size}
        height={size}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="animate-pulse"
      >
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M24 4C23.5 4 23 4.5 23 5V12L21 9C20.5 8.2 19.8 7.5 19 7.5C18 7.5 17.5 8.2 17.5 9V16C17.5 17 16.8 17.8 16 17.8C15 17.8 14.5 17 14.5 16V11C14.5 10 14 9.5 13 9.5C12 9.5 11.5 10 11.5 11V18C11.5 20 12.5 22 14.5 23L17 24L19 30L21 42C21 43.5 22 45 23.5 45H24.5C26 45 27 43.5 27 42L29 30L31 24L33.5 23C35.5 22 36.5 20 36.5 18V11C36.5 10 36 9.5 35 9.5C34 9.5 33.5 10 33.5 11V16C33.5 17 33 17.8 32 17.8C31.2 17.8 30.5 17 30.5 16V9C30.5 8.2 30 7.5 29 7.5C28.2 7.5 27.5 8.2 27 9L25 12V5C25 4.5 24.5 4 24 4ZM22.5 18H25.5V40H22.5V18Z"
          fill="#000000"
        />
      </svg>
    </div>
  );
}

