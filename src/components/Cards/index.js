import React from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

/**
 * Responsive navigation card grid for MDX. Pair with <Card>.
 *
 * <CardGrid columns={3}>
 *   <Card to="/quickstart" icon="🧩" eyebrow="dApp developers"
 *         title="Build cross-rollup apps" cta="Quickstart">
 *     One-line description.
 *   </Card>
 * </CardGrid>
 */
export function CardGrid({children, columns = 3}) {
  return (
    <div className={styles.grid} style={{'--card-columns': String(columns)}}>
      {children}
    </div>
  );
}

/**
 * A single navigation card. `to` accepts an internal doc route or an external
 * URL (Docusaurus <Link> handles both). `accent` renders a filled brand-green
 * card for primary calls-to-action.
 */
export function Card({to, icon, eyebrow, title, cta, accent = false, children}) {
  return (
    <Link className={`${styles.card} ${accent ? styles.accent : ''}`} to={to}>
      {icon ? (
        <span className={styles.icon} aria-hidden="true">
          {icon}
        </span>
      ) : null}
      {eyebrow ? <span className={styles.eyebrow}>{eyebrow}</span> : null}
      <span className={styles.title}>{title}</span>
      {children ? <span className={styles.body}>{children}</span> : null}
      {cta ? <span className={styles.cta}>{cta} →</span> : null}
    </Link>
  );
}

export default Card;
