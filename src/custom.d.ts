// This file is used to declare modules for non-TypeScript files like CSS modules.

declare module '*.module.css' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

declare module '@theme/Layout' {
  import type { ComponentType, ReactNode } from 'react';

  interface Props {
    children: ReactNode;
    title?: string;
    description?: string;
  }

  const Layout: ComponentType<Props>;
  export default Layout;
}
