import Form from "../components/Form"
import Layout from "../components/Layout"

function Register() {
    return (
        <Layout>
            <div className="flex justify-center items-center h-[calc(100vh-200px)]">
                <Form route="/api/register/" method="register" />
            </div>
        </Layout>
    )
}

export default Register
