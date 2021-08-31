import { Link } from "gatsby";
import * as React from "react";
import Navigation from "../components/Navigation";
import Grapejuice from "../images/grapejuice.svg";
import "../styles/global.scss";
import "../styles/layout/main-layout.scss";

const MainLayout = ({ children }) => {
    return (
        <div class="page main-layout">
            <header class="page-header">
                <section class="branding">
                    <Link to="/">
                        <img src={Grapejuice} height={48} />
                        <span>
                            Grapejuice
                        </span>
                        <span class="aligner">

                        </span>
                    </Link>
                </section>

                <Navigation></Navigation>
            </header>

            <main>
                {children}
            </main>
        </div>
    );
};

export default MainLayout;
