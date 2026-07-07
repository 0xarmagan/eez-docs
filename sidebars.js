// @ts-check

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.

 @type {import('@docusaurus/plugin-content-docs').SidebarsConfig}
 */
const sidebars = {
  docsSidebar: [
    {
      type: 'category',
      label: 'Get Started',
      items: ['introduction', 'quickstart', 'architecture'],
    },
    {
      type: 'category',
      label: 'Core Concepts',
      items: [
        'concepts/sync-composability',
        'concepts/execution-model',
        'concepts/rolling-hash',
        'concepts/multi-prover',
        'concepts/cross-chain-proxy',
      ],
    },
  ],
};

export default sidebars;
