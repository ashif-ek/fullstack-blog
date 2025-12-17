import { Link } from "react-router-dom"

function PostCard({ post, onDelete }) {
    const formattedDate = new Date(post.created_at).toLocaleDateString("en-US", {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    })

    return (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6 hover:shadow-lg transition duration-300">
            <h2 className="text-2xl font-bold mb-2 text-gray-800 hover:text-blue-600 transition duration-300">
                <Link to={`/post/${post.id}`}>{post.title}</Link>
            </h2>
            <p className="text-gray-600 text-sm mb-4">By {post.author} on {formattedDate}</p>
            <p className="text-gray-700 leading-relaxed mb-4 line-clamp-3">
                {post.content}
            </p>
            <div className="flex justify-between items-center">
                <Link to={`/post/${post.id}`} className="text-blue-500 hover:underline font-semibold">Read more</Link>
                <button 
                    onClick={() => onDelete(post.id)} 
                    className="text-red-500 hover:text-red-700 font-semibold text-sm bg-red-50 px-3 py-1 rounded"
                >
                    Delete
                </button>
            </div>
        </div>
    )
}

export default PostCard
