import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

type Props = {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  y?: number;
  duration?: number;
};

export default function FadeIn({ children, className = '', delay = 0, y = 20, duration = 0.6 }: Props) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const animationsDisabled = typeof window !== 'undefined' && window.localStorage?.getItem('animations') === 'off';
    if (animationsDisabled) {
      // directly set final state
      if (ref.current) {
        ref.current.style.opacity = '1';
        ref.current.style.transform = 'translateY(0px)';
      }
      return;
    }
    const el = ref.current;
    if (!el) return;

    gsap.fromTo(
      el,
      { opacity: 0, y },
      {
        opacity: 1,
        y: 0,
        duration,
        ease: 'power3.out',
        delay,
        scrollTrigger: {
          trigger: el,
          start: 'top 95%',
        },
      }
    );

    return () => {
      // kill ScrollTrigger instances attached to this element
      ScrollTrigger.getAll().forEach((st) => {
        if (st.trigger === el) st.kill();
      });
    };
  }, [delay, y, duration]);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}
