import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';

type Props = {
  text: string;
  className?: string;
  delay?: number;
  duration?: number;
  stagger?: number;
};

export default function BlurText({ text, className = '', delay = 0, duration = 0.9, stagger = 0.03 }: Props) {
  const ref = useRef<HTMLSpanElement | null>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const animationsDisabled = typeof window !== 'undefined' && window.localStorage?.getItem('animations') === 'off';

    const chars = Array.from(el.querySelectorAll('.bt-char')) as HTMLElement[];

    if (animationsDisabled) {
      chars.forEach((c) => {
        c.style.opacity = '1';
        c.style.transform = 'translateY(0px)';
        c.style.filter = 'blur(0px)';
      });
      return;
    }

    // initial state
    gsap.set(chars, { opacity: 0, y: 6, filter: 'blur(6px)' });

    gsap.to(chars, {
      opacity: 1,
      y: 0,
      filter: 'blur(0px)',
      duration,
      ease: 'power3.out',
      stagger,
      delay,
    });

    return () => {
      gsap.killTweensOf(chars as any);
    };
  }, [text, delay, duration, stagger]);

  return (
    <span ref={ref} className={className} aria-hidden>
      {text.split('').map((ch, i) => (
        <span key={i} className="bt-char inline-block">
          {ch === ' ' ? '\u00A0' : ch}
        </span>
      ))}
    </span>
  );
}
