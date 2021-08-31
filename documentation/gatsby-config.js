module.exports = {
    siteMetadata: {
        siteUrl: "https://www.yourdomain.tld",
        title: "Grapejuice",
    },
    plugins: [
        "gatsby-plugin-sass",
        {
            resolve: "gatsby-plugin-manifest",
            options: {
                icon: "src/images/icon.png",
            },
        },
        "gatsby-plugin-mdx",
        {
            resolve: "gatsby-source-filesystem",
            options: {
                name: "pages",
                path: "./src/pages/",
            },
            __key: "pages",
        },
        "gatsby-plugin-root-import"
    ],
};
