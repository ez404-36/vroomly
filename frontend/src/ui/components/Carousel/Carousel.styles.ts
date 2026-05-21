export const carouselContainer = 'relative overflow-hidden';

export const carouselTrack = 'flex gap-4 overflow-x-auto scroll-smooth snap-x snap-mandatory scrollbar-hide';

export const carouselTrackHidden = 'scrollbar-hide [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden';

export const carouselNavButton =
  'absolute top-1/2 -translate-y-1/2 z-10 flex h-10 w-10 items-center justify-center rounded-full bg-(--color-surface) border border-(--color-border) shadow-md hover:bg-(--color-bg-muted) disabled:opacity-50 disabled:cursor-not-allowed transition-colors';

export const carouselNavButtonPrev = 'left-2';

export const carouselNavButtonNext = 'right-2';

export const carouselNavIcon = 'h-5 w-5 text-(--color-text)';

export const carouselSingleItem = 'flex items-center justify-center w-full min-h-[220px] relative overflow-hidden';

export const carouselSingleInner = 'transition-all duration-300 ease-in-out';