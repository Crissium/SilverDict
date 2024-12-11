import { defineConfig, transformWithEsbuild } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
	server: {
		host: '0.0.0.0',
		proxy: {
			'/api': 'http://127.0.0.1:2628'
		}
	},

	plugins: [
		react(),

		// Workaround
		{
			name: 'load+transform-js-files-as-jsx',
			async transform(code, id) {
				if (!id.match(/src\/.*\.js$/)) {
					return null;
				}

				// Use the exposed transform from vite, instead of directly
				// transforming with esbuild
				return transformWithEsbuild(code, id, {
					loader: 'jsx',
					jsx: 'automatic', // this is important
				});
			},
		},
		// End workaround
	],

	// Workaround before renaming .js to .jsx
	optimizeDeps: {
		esbuildOptions: {
			loader: {
				'.js': 'jsx',
			},
		},
	},
	// End workaround

	base: '/silverdict',

	build: {
		outDir: 'build',
		rollupOptions: {
			output: {
				manualChunks(id) {
					if (id.includes('node_modules')) {
						return id.toString().split('node_modules/')[1].split('/')[0].toString();
					}
				},
				// Don't append hashes to filenames, anyway we only generate one index.js and there definitely won't be a conflict with other files
				entryFileNames: `assets/[name].js`,
				chunkFileNames: `assets/[name].js`,
				assetFileNames: `assets/[name].[ext]`
			}
		}
	}
});
