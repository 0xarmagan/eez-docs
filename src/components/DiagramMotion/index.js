import React, {useEffect, useState} from 'react';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './styles.module.css';

/**
 * Docs-embedded motion loop. Renders an autoplay/muted/looping <video> on a dark
 * panel (matching the always-dark Mermaid diagrams), and falls back to the poster
 * still when the reader prefers reduced motion. Assets live in static/motion/.
 *
 * <DiagramMotion src="/motion/what-is-eez.webm" poster="/motion/what-is-eez-poster.png"
 *   alt="…" caption="…" />
 */
export default function DiagramMotion({src, poster, alt = '', caption}) {
  const videoUrl = useBaseUrl(src);
  const posterUrl = useBaseUrl(poster);
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return undefined;
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReduced(mq.matches);
    const onChange = (e) => setReduced(e.matches);
    mq.addEventListener?.('change', onChange);
    return () => mq.removeEventListener?.('change', onChange);
  }, []);

  return (
    <figure className={styles.wrap}>
      <div className={styles.panel}>
        {reduced ? (
          <img className={styles.media} src={posterUrl} alt={alt} />
        ) : (
          <video
            className={styles.media}
            src={videoUrl}
            poster={posterUrl}
            autoPlay
            muted
            loop
            playsInline
            aria-label={alt}
          />
        )}
      </div>
      {caption ? <figcaption className={styles.caption}>{caption}</figcaption> : null}
    </figure>
  );
}
