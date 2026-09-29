CREATE TABLE `storages` (
	`id` text PRIMARY KEY NOT NULL,
	`type` text NOT NULL,
	`connection` text,
	`path` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `video_files` (
	`id` text PRIMARY KEY NOT NULL,
	`storage_id` text NOT NULL,
	`mtime` integer NOT NULL,
	`raw_path` text NOT NULL,
	`raw_size` integer NOT NULL,
	`event_type` text NOT NULL,
	`direction` text NOT NULL,
	`timestamp` integer NOT NULL,
	FOREIGN KEY (`storage_id`) REFERENCES `storages`(`id`) ON UPDATE no action ON DELETE no action
);
