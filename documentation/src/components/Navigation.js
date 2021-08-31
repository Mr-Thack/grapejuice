import { Link } from "gatsby";
import * as React from "react";
import "../styles/components/navigation.scss";

const Navigation = () => {
    return (
        <nav>
            <ul>
                <li>
                    <Link to="/">Home</Link>
                </li>
                <li>
                    <Link to="/docs">Documentation</Link>
                </li>
            </ul>
        </nav>
    );
};

export default Navigation
