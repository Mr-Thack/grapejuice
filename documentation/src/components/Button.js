import * as React from "react";
import "../styles/components/button.scss";

const Button = ({ children }) => {
    return (
        <span class="button">
            {children}
        </span>
    );
}

export default Button;
