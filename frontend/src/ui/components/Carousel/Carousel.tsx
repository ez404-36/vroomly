import React, { useRef, useEffect, useState, useCallback } from 'react';
import { clsx } from 'clsx';
import {
  carouselContainer,
  carouselNavButton,
  carouselNavButtonNext,
  carouselNavButtonPrev,
  carouselNavIcon,
  carouselTrack,
  carouselTrackHidden,
  carouselSingleItem,
  carouselSingleInner,
} from './Carousel.styles';
import type { CarouselProps } from './Carousel.types';

export const Carousel = ({ children, className, singleItem = false, onIndexChange, initialIndex = 0 }: CarouselProps) => {
  const trackRef = useRef<HTMLDivElement>(null);
  const [currentIndex, setCurrentIndex] = useState(initialIndex);
  const [slideDirection, setSlideDirection] = useState<'left' | 'right' | null>(null);
  const [showNavButtons, setShowNavButtons] = useState(false);

  // Convert children to array for easier handling
  const childrenArray = React.Children.toArray(children);
  const totalItems = childrenArray.length;

  // Sync with parent if initialIndex changes
  useEffect(() => {
    setCurrentIndex(initialIndex);
  }, [initialIndex]);

  // Check if content overflows and navigation is needed
  const checkOverflow = useCallback(() => {
    if (trackRef.current) {
      const { scrollWidth, clientWidth } = trackRef.current;
      if (singleItem) {
        // Single item mode: show buttons only if more than 1 item
        setShowNavButtons(totalItems > 1);
      } else {
        // Normal mode: show buttons only if content overflows
        setShowNavButtons(scrollWidth > clientWidth + 1); // +1 for subpixel rendering
      }
    } else if (singleItem) {
      setShowNavButtons(totalItems > 1);
    }
  }, [singleItem, totalItems]);

  useEffect(() => {
    checkOverflow();
    
    // Re-check on resize
    const handleResize = () => checkOverflow();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [checkOverflow, childrenArray.length]);

  // Re-check after children render
  useEffect(() => {
    const timer = setTimeout(checkOverflow, 100);
    return () => clearTimeout(timer);
  }, [checkOverflow, childrenArray.length]);

  const scrollBy = (direction: 'left' | 'right') => {
    if (totalItems === 0) return;

    let newIndex: number;
    if (singleItem) {
      newIndex = direction === 'left'
        ? (currentIndex - 1 + totalItems) % totalItems
        : (currentIndex + 1) % totalItems;
    } else {
      newIndex = direction === 'left'
        ? Math.max(0, currentIndex - 1)
        : Math.min(totalItems - 1, currentIndex + 1);
    }

    setSlideDirection(direction);
    setCurrentIndex(newIndex);
    onIndexChange?.(newIndex);

    // Reset slide direction after animation
    setTimeout(() => setSlideDirection(null), 300);
  };

  // Smooth scroll for non-singleItem mode
  useEffect(() => {
    if (!singleItem && trackRef.current && totalItems > 0) {
      const childElement = trackRef.current.children[currentIndex] as HTMLElement;
      if (childElement) {
        trackRef.current.style.scrollBehavior = 'smooth';
        childElement.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      }
    }
  }, [currentIndex, singleItem, totalItems]);

  return (
    <div className={clsx(carouselContainer, className)}>
      {showNavButtons && (
        <button
          type="button"
          onClick={() => scrollBy('left')}
          className={clsx(carouselNavButton, carouselNavButtonPrev)}
          aria-label="Previous"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={carouselNavIcon}
          >
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>
      )}

      {singleItem ? (
        <div className={clsx(carouselSingleItem)}>
          <div
            key={currentIndex}
            className={clsx(
              carouselSingleInner,
              slideDirection === 'left' && 'animate-slide-left',
              slideDirection === 'right' && 'animate-slide-right',
            )}
          >
            {childrenArray[currentIndex]}
          </div>
        </div>
      ) : (
        <div
          ref={trackRef}
          className={clsx(carouselTrack, carouselTrackHidden)}
          onScroll={checkOverflow}
        >
          {childrenArray}
        </div>
      )}

      {showNavButtons && (
        <button
          type="button"
          onClick={() => scrollBy('right')}
          className={clsx(carouselNavButton, carouselNavButtonNext)}
          aria-label="Next"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={carouselNavIcon}
          >
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>
      )}
    </div>
  );
};