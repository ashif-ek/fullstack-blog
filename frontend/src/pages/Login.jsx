import Form from "../components/Form"
import Layout from "../components/Layout"

function Login() {
    return (
        <Layout>
            <div className="flex justify-center items-center h-[calc(100vh-200px)]">
                <Form route="/api/token/" method="login" />
            </div>
        </Layout>
    )
}

export default Login
