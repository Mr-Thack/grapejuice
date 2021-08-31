import { Link } from "gatsby"
import * as React from "react"
import Button from "../components/Button"
import Grapejuice from "../images/grapejuice.svg"
import MainLayout from "../layout/MainLayout"
import "../styles/index.scss"

const IndexPage = () => {
    return (
        <MainLayout>
            <section class="hero">
                <h1 class="align-center">
                    <img src={Grapejuice} />
                    <span>Grapejuice</span>
                    <small>
                        Running Roblox on Linux, made easy
                    </small>
                </h1>
            </section>

            <div class="align-center">
                <Link to="/docs">
                    <Button>
                        Get started
                    </Button>
                </Link>
            </div>
        </MainLayout>
    )
}

export default IndexPage
