'use strict';

module.exports = function(grunt) {
	grunt.initConfig({
		jade: {
			compile: {
				options: {
					pretty: true
				},
				files: {
					'pub/main.html': 'src/main.jade'
				}
			}
		},
		coffee: {
			compile: {
				files: {
					'pub/js/main.js': 'src/main.coffee',
					'pub/js/graph.js': 'src/graph.coffee',
					'pub/js/indented_tree.js': 'src/indented_tree.coffee'
				},
				options: {
					bare: true
				}
			}
		}
	});

	grunt.loadNpmTasks('grunt-contrib-jade');
	grunt.loadNpmTasks('grunt-contrib-coffee');

	// A very basic default task.
	grunt.registerTask('build', ['jade', 'coffee']);

	grunt.registerTask('default', ['build']);
};