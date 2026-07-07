// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Ethereum Economic Zone',
  tagline: 'EEZ enables atomic cross-chain calls between Ethereum rollups in a single L1 block.',
  favicon: 'img/01-mark-on-black.png',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
    // Keep disabled: the Rspack/SWC "faster" pipeline silently drops the
    // Mermaid remark transform (diagrams fall back to plain code blocks
    // with zero build warning). Re-verify with a real diagram before ever
    // re-enabling.
    faster: false,
  },

  // Set the production url of your site here
  url: 'https://eez-docs.vercel.app',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'eez-association', // Usually your GitHub org/user name.
  projectName: 'eez-docs', // Usually your repo name.

  onBrokenLinks: 'throw',

  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          routeBasePath: '/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'contracts',
        path: 'contracts',
        routeBasePath: 'contracts',
        sidebarPath: './sidebarsContracts.js',
      },
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/eez-logo.png',
      // EEZ brand indigo palette (matches src/css/custom.css). Mermaid's
      // `options` (themeVariables) is shared across light/dark modes — a
      // light-card look (light fills, dark indigo text/lines) reads well
      // against both page backgrounds, so `base` is used for both.
      mermaid: {
        theme: {light: 'base', dark: 'base'},
        options: {
          themeVariables: {
            primaryColor: '#E0E7FF',
            primaryTextColor: '#312E81',
            primaryBorderColor: '#6366F1',
            lineColor: '#6366F1',
            secondaryColor: '#C7D2FE',
            tertiaryColor: '#EEF2FF',
            actorBkg: '#E0E7FF',
            actorBorder: '#6366F1',
            actorTextColor: '#312E81',
            actorLineColor: '#818CF8',
            signalColor: '#4338CA',
            signalTextColor: '#312E81',
            labelBoxBkgColor: '#C7D2FE',
            labelBoxBorderColor: '#6366F1',
            labelTextColor: '#312E81',
            noteBkgColor: '#EEF2FF',
            noteBorderColor: '#818CF8',
            noteTextColor: '#312E81',
            loopTextColor: '#4338CA',
            activationBkgColor: '#C7D2FE',
            activationBorderColor: '#6366F1',
            sequenceNumberColor: '#312E81',
            fontFamily: 'inherit',
            actorFontSize: '15px',
            messageFontSize: '15px',
            noteFontSize: '14px',
          },
        },
      },
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'EEZ',
        logo: {
          alt: 'EEZ Logo',
          src: 'img/eez-logo.png',
        },
        items: [
          {
            type: 'doc',
            docId: 'introduction',
            docsPluginId: 'default',
            position: 'left',
            label: 'Documentation',
          },
          {
            type: 'doc',
            docId: 'eez',
            docsPluginId: 'contracts',
            position: 'left',
            label: 'Contract Reference',
          },
          {
            href: 'https://github.com/eez-association/eez-core-protocol',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Community',
            items: [
              {label: 'GitHub', href: 'https://github.com/eez-association'},
              {label: 'Website', href: 'https://eez.io/'},
              {label: 'X', href: 'https://x.com/etheconomiczone'},
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Ethereum Economic Zone.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
