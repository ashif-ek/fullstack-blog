import { Link } from "react-router-dom"

function PostCard({ post, onDelete }) {
    const formattedDate = new Date(post.created_at).toLocaleDateString("en-US", {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    })

    return (
        <div className="group bg-white border border-gray-200 hover:border-red-200 hover:shadow-sm transition-all duration-300">
            {post.image && (
                <div className="h-56 overflow-hidden relative border-b border-gray-100">
                    <img 
                        src={post.image.startsWith('http') ? post.image : `${import.meta.env.VITE_API_URL}${post.image}`} 
                        alt={post.title} 
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" 
                    />
                </div>
            )}
            
            <div className="p-8">
                <div className="flex justify-between items-start mb-4">
                    <h2 className="text-2xl font-serif font-bold text-slate-900 leading-tight group-hover:text-red-700 transition duration-300">
                        <Link to={`/post/${post.id}`}>
                            {post.title}
                        </Link>
                    </h2>
                </div>
                
                <div className="text-xs font-sans font-bold uppercase tracking-widest text-slate-500 mb-6">
                    <span className="text-slate-900">{post.author}</span> • {formattedDate}
                </div>
 
                <p className="text-slate-700 font-serif leading-relaxed line-clamp-3 mb-6">
                    {post.content}
                </p>
 
                <div className="flex justify-between items-center pt-6 border-t border-gray-100">
                    <Link to={`/post/${post.id}`} className="text-red-700 hover:text-red-800 font-bold text-xs uppercase tracking-widest transition duration-300">
                        Read Abstract →
                    </Link>
                    <button 
                        onClick={() => onDelete(post.id)} 
                        className="text-slate-400 hover:text-red-500 font-bold text-[10px] uppercase tracking-widest transition duration-300"
                    >
                        Delete
                    </button>
                </div>
            </div>
        </div>
    )
}

export default PostCard;
