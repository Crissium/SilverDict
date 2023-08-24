const transpileDependencies = true
const devServer = {
	proxy: {
		'/api/*': {
			target: 'http://localhost:5000',
			secure: false,
			changeOrigin: true
		}
	}
}

// Deploying to GitHub Pages
// module.exports = {
// 	publicPath: '/SilverDict/'
// }