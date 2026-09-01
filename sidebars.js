// @ts-check

/**
 * The site is a mirror of eez-core-protocol/docs (pinned at commit 9735f53),
 * plus three "Get started" pages that exist only as landing points for the
 * three target audiences on the introduction page.
 *
 * Everything under "Specification" is transferred from upstream — the section
 * order follows the source repo's own layout, and CORE_PROTOCOL_SPEC.md is
 * split into its nine A–I sections so each is independently navigable.
 *
 * @type {import('@docusaurus/plugin-content-docs').SidebarsConfig}
 */
const sidebars = {
  docsSidebar: [
    {
      type: 'category',
      label: 'Get Started',
      collapsed: false,
      items: ['introduction', 'quickstart', 'architecture', 'register-rollup'],
    },
    {
      type: 'category',
      label: 'Core Protocol Spec',
      link: {type: 'doc', id: 'spec/core-protocol/index'},
      items: [
        'spec/core-protocol/a-data-model',
        'spec/core-protocol/b-protocol-functions',
        'spec/core-protocol/c-action-hash',
        'spec/core-protocol/d-execution-model',
        'spec/core-protocol/e-rolling-hash',
        'spec/core-protocol/f-static-entry-resolution',
        'spec/core-protocol/g-entry-lifecycle',
        'spec/core-protocol/h-invariants',
        'spec/core-protocol/i-security-considerations',
      ],
    },
    {
      type: 'category',
      label: 'Entry Specs',
      collapsed: false,
      items: ['spec/execution-entries', 'spec/static-entries'],
    },
    {
      type: 'category',
      label: 'Proving',
      collapsed: false,
      items: ['spec/multi-prover'],
    },
    {
      type: 'category',
      label: 'Blob Format',
      items: [
        'spec/blobs/blob-format',
        'spec/blobs/u256-codec',
        'spec/blobs/future-optimizations',
      ],
    },
    {
      type: 'category',
      label: 'Reference',
      items: ['spec/caveats'],
    },
  ],
};

export default sidebars;
