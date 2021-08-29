import { Link } from "gatsby"
import * as React from "react"
import "../styles/index.scss"

const IndexPage = () => {
    return (
        <div class="page">
            <header>
                <section class="branding">
                    Grapejuice
                </section>

                <nav>
                    <ul>
                        <li>
                            <Link to="index">Home</Link>
                        </li>
                        <li>
                            <Link to="docs">Documentation</Link>
                        </li>
                    </ul>
                </nav>
            </header>

            <main>
                <section class="hero">
                    <h1>
                        <span>Grapejuice</span>
                        <small>
                            Running Roblox on Linux, made easy
                        </small>
                    </h1>
                </section>

                <span class="button">
                    Get started
                </span>
            </main>
        </div>
    )
}

export default IndexPage
