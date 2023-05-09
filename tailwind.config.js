/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		'./templates/**/*.html',
		// Templates in other apps ( the app name needs to end with _app)
		'./*_app/templates/**/*.html',
		// for flowbite config
		'./node_modules/flowbite/**/*.js',
		// Ignore files in node_modules
		// '!../**/node_modules',
		// '!../**/node_modules',
		// Include JavaScript files that might contain Tailwind CSS classes
		// '../**/*.js',
		// Include Python files that might contain Tailwind CSS classes
		// '../**/*.py',
	],
	theme: {
		extend: {},
	},
	plugins: [require('flowbite/plugin')],
}
