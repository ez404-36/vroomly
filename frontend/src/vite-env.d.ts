declare module '*.svg' {
  import type { ComponentType, SVGProps } from 'react';

  const content: ComponentType<SVGProps<SVGSVGElement>>;
  export default content;
  export const ReactComponent: ComponentType<SVGProps<SVGSVGElement>>;
}

declare module '*?react' {
  import type { ComponentType, SVGProps } from 'react';

  const content: ComponentType<SVGProps<SVGSVGElement>>;
  export default content;
}