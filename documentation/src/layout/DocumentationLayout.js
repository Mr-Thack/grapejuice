import * as React from "react";
import "../styles/global.scss";
import "../styles/layout/main-layout.scss";
import MainLayout from "./MainLayout";

const DocumentationLayout = ({ children }) => {
    return (
        <MainLayout>
            {children}
        </MainLayout>
    );
};

export default DocumentationLayout
