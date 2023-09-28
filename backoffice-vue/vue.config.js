const webpack = require('webpack')
// const CircularDependencyPlugin = require('circular-dependency-plugin')

module.exports = {
  runtimeCompiler: true,
  productionSourceMap: false,
  lintOnSave: false,
  devServer: {
    allowedHosts: "all",
  },
  configureWebpack: {
    resolve: {
      extensions: ['.js'],
      alias: {
        jquery: 'jquery/dist/jquery.min.js',
      },
    },
    module: {
      rules: [
        {
          test: /\.coffee$/,
          loader: "coffee-loader",
        },
      ],
    },
    plugins: [
      new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery',
        Popper: ['popper.js', 'default'],
        Util: "exports-loader?Util!bootstrap/js/dist/util",
      }),
      // ,
      // new CircularDependencyPlugin({
      //   // exclude detection of files based on a RegExp
      //   exclude: /a\.js|node_modules/,
      //   // add errors to webpack instead of warnings
      //   failOnError: false,
      //   // set the current working directory for displaying module paths
      //   cwd: process.cwd()
      // })
    ],
  },
}
