// @ts-check
import { themes as prismThemes } from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Bridging the gap between the digital brain and the physical body',
  url: 'https://hackathon-1-q4.vercel.app',
  baseUrl: '/',
  onBrokenLinks: 'throw',

  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  favicon: 'img/favicon.ico',

  organizationName: 'panaversity',
  projectName: 'physical-ai-humanoid-textbook',

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ur'],
    localeConfigs: {
      en: {
        label: 'English',
        direction: 'ltr',
        htmlLang: 'en-US',
        calendar: 'gregory',
        path: 'en',
      },
      ur: {
        label: 'اردو',
        direction: 'rtl', // Urdu is a right-to-left language
        htmlLang: 'ur-PK',
        calendar: 'gregory',
        path: 'ur',
      },
    },
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.ts'),
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
        // IMPORTANT: For i18n, always ensure there is a docs plugin instance for each locale
        // If you are using `docusaurus-plugin-content-docs` in advanced mode (not in preset-classic)
        // you would configure instances for each locale.
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'Physical AI & Robotics',
        logo: {
          alt: 'The Digital Ark Logo',
          src: 'img/logo-ark.png',
          width: 40,
          height: 40,
        },
        items: [
          { type: 'docSidebar', sidebarId: 'tutorialSidebar', position: 'left', label: 'Docs' },
          { to: '/biography', label: 'Biography', position: 'left' },
          { to: '/chat', label: 'Ask the AI', position: 'left' },
          {
            href: 'https://www.linkedin.com/in/ghulam-sarwar-khan-b989b48a',
            label: 'LinkedIn',
            position: 'right',
          },
          {
            href: 'https://www.facebook.com/sarwaronline/',
            label: 'Facebook',
            position: 'right',
          },
          { href: 'https://github.com/gsarwarkhan/Hackathon-1-Q4', label: 'GitHub', position: 'right' },
          {
            type: 'localeDropdown',
            position: 'right',
          },
          {
            type: 'html',
            position: 'right',
            value: '<img src="/img/profile.png" style="width: 44px; height: 44px; border-radius: 50%; border: 3px solid #764ba2; display: block; margin-top: 0px; box-shadow: 0 0 10px rgba(118, 75, 162, 0.3);" alt="Ghulam Sarwar Khan" />',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Read Textbook',
                to: '/docs',
              },
            ],
          },
          {
            title: 'Community & Social',
            items: [
              {
                label: 'LinkedIn',
                href: 'https://www.linkedin.com/in/ghulam-sarwar-khan-b989b48a',
              },
              {
                label: 'Facebook',
                href: 'https://www.facebook.com/sarwaronline/',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/gsarwarkhan/Hackathon-1-Q4',
              },
            ],
          },
        ],
        copyright: `© ${new Date().getFullYear()} Panaversity Physical AI. Built by Ghulam Sarwar Khan.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;