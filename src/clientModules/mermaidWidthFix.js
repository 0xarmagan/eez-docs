// Mermaid SVGs render with `width="100%"` and no height attribute — only a
// viewBox providing an intrinsic ratio, no intrinsic width/height. Per the
// CSS replaced-element sizing algorithm, that makes even `width: auto`
// resolve to the containing block's width, silently shrinking wide
// horizontal diagrams to illegibility in a narrow docs column. Force each
// mermaid SVG to its own viewBox pixel width so `overflow-x: auto` on
// `.docusaurus-mermaid-container` can scroll it instead of squeezing it.
function fixMermaidSvgWidths() {
  document.querySelectorAll('.docusaurus-mermaid-container svg').forEach((svg) => {
    const box = svg.viewBox && svg.viewBox.baseVal;
    if (box && box.width > 0) {
      const target = `${box.width}px`;
      if (svg.style.width !== target) {
        svg.style.width = target;
      }
    }
  });
}

if (typeof window !== 'undefined') {
  const observer = new MutationObserver(fixMermaidSvgWidths);
  const start = () => {
    fixMermaidSvgWidths();
    observer.observe(document.body, {childList: true, subtree: true});
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
}

export function onRouteDidUpdate() {
  if (typeof window !== 'undefined') {
    setTimeout(fixMermaidSvgWidths, 300);
  }
}
