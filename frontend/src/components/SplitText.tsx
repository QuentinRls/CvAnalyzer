import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

type Props = {
  text: string;
  className?: string;
  delay?: number;
};

export default function SplitText({ text, className = '', delay = 0 }: Props) {
  const ref = useRef<HTMLSpanElement | null>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const animationsDisabled = typeof window !== 'undefined' && window.localStorage?.getItem('animations') === 'off';

    const chars = el.querySelectorAll('.char');

    if (animationsDisabled) {
      // set final visible state
      chars.forEach((c) => {
        (c as HTMLElement).style.opacity = '1';
        (c as HTMLElement).style.transform = 'translateY(0px)';
      });
      return;
    }

    gsap.set(chars, { opacity: 0, y: 30 });

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: el,
        start: 'top 80%'
      }
    });

    tl.to(chars, {
      duration: 0.6,
      y: 0,
      opacity: 1,
      stagger: 0.03,
      ease: 'power3.out',
      delay
    });

    return () => {
      tl.kill();
    };
  }, [text, delay]);

  return (
    <span ref={ref} className={className} aria-hidden>
      {text.split('').map((c, i) => (
        <span key={i} className="char inline-block will-change-transform">
          {c === ' ' ? '\u00A0' : c}
        </span>
      ))}
    </span>
  );
}
