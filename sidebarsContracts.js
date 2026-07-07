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
    {
      type: 'category',
      label: 'L2 Contracts',
      items: ['eezl2'],
    },
    {
      type: 'category',
      label: 'Data Types',
      items: ['data-types'],
    },
  ],
};

export default sidebarsContracts;
