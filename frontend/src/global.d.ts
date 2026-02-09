/// <reference types="next" />
/// <reference types="next/image-types/global" />

// CSS Module declarations (*.module.css, *.module.scss, etc.)
declare module '*.module.css' {
  const classes: { [key: string]: string };
  export default classes;
}

declare module '*.module.scss' {
  const classes: { [key: string]: string };
  export default classes;
}

declare module '*.module.sass' {
  const classes: { [key: string]: string };
  export default classes;
}

// Global CSS side-effect imports (*.css, *.scss, etc.)
declare module '*.css';
declare module '*.scss';
declare module '*.sass';
