import { Link } from "gatsby";
import * as React from "react";
import MainLayout from "../../layout/MainLayout";

const DocumentationIndex = () => {
    return (
        <MainLayout>
            <section>
                <header>
                    <h1>Install Grapejuice locally from Source</h1>
                </header>

                <ul>
                    <li>
                        <Link to="/docs/source-install/archlinux">Arch Linux</Link>
                    </li>
                    <li>
                        <Link to="/docs/source-install/debian-10">Debian 10 and Similar</Link>
                    </li>
                    <li>
                        <Link to="/docs/source-install/fedora-workstation">Fedora Workstation</Link>
                    </li>
                    <li>
                        <Link to="/docs/source-install/solus">Solus</Link>
                    </li>
                    <li>
                        <Link to="/docs/source-install/ubuntu-1804">Ubuntu 18.04</Link>
                    </li>
                </ul>
            </section>
        </MainLayout>
    );
}

export default DocumentationIndex;
