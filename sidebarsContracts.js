// @ts-check

/**
 * Sidebar for the Contract Reference docs instance.
 *
 * @type {import('@docusaurus/plugin-content-docs').SidebarsConfig}
 */
const sidebarsContracts = {
  contractsSidebar: [
    {
      type: 'category',
      label: 'L1 Contracts',
      items: ['eez', 'rollup', 'bridge'],
    },
  ],
};

export default sidebarsContracts;
