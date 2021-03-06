<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the
 * installation. You don't have to use the web site, you can
 * copy this file to "wp-config.php" and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * MySQL settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://codex.wordpress.org/Editing_wp-config.php
 *
 * @package WordPress
 */

//include local settings, if they exist
if ( file_exists( dirname( __FILE__ ) . '/wp-config-local.php' ) )
	include( dirname( __FILE__ ) . '/wp-config-local.php' );
else
    //there always must be production settings
	require('wp-config-live.php');

//home is site url by convention
define('WP_HOME', WP_SITEURL);


//caching (obviously works only with wp-super-cache) 
define('WPCACHEHOME', dirname(__FILE__) . '/wp-content/plugins/wp-super-cache/');
//enable cache only for production environment
if(!defined('WP_CACHE'))
    define('WP_CACHE', true);


/** Database Charset to use in creating database tables. */
define('DB_CHARSET', 'utf8');

/** The Database Collate type. Don't change this if in doubt. */
define('DB_COLLATE', '');

/**#@+
 * Authentication Unique Keys and Salts.
 *
 * Change these to different unique phrases!
 * You can generate these using the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}
 * You can change these at any point in time to invalidate all existing cookies. This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
//this file holds the salt definitions.
require('wp-salt.php');

/**#@-*/

/**
 * WordPress Database Table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix  = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the Codex.
 *
 * @link https://codex.wordpress.org/Debugging_in_WordPress
 */
//wp debug might have been defined in a local environment. However, this file contains the settings for production, so we generally want to turn debug off
if(!defined('WP_DEBUG'))
    define('WP_DEBUG', false);
if(!defined('WP_DEBUG_DISPLAY'))
    define('WP_DEBUG_DISPLAY', false);

if ( file_exists( dirname( __FILE__ ) . '/wp-config-custom.php' ) )
	include( dirname( __FILE__ ) . '/wp-config-custom.php' );

/* That's all, stop editing! Happy blogging. */

/** Absolute path to the WordPress directory. */
if ( !defined('ABSPATH') )
	define('ABSPATH', dirname(__FILE__) . '/');

/** Sets up WordPress vars and included files. */
require_once(ABSPATH . 'wp-settings.php');
