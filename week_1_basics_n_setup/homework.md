## Week 1 Homework

In this homework we'll prepare the environment 
and practice with terraform and SQL


## Question 1. Google Cloud SDK

Install Google Cloud SDK. What's the version you have? 

To get the version, run `gcloud --version`

## Google Cloud account 

Create an account in Google Cloud and create a project.


## Question 2. Terraform 

Now install terraform and go to the terraform directory (`week_1_basics_n_setup/1_terraform_gcp/terraform`)

After that, run

* `terraform init`
* `terraform plan`
* `terraform apply` 

Apply the plan and copy the output (after running `apply`) to the form.

It should be the entire output - from the moment you typed `terraform init` to the very end.

## Prepare Postgres 

Run Postgres and load data as shown in the videos

We'll use the yellow taxi trips from January 2021:

```bash
wget https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2021-01.csv
```

You will also need the dataset with zones:

```bash 
wget https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv
```

Download this data and put it to Postgres

## Question 3. Count records 

How many taxi trips were there on January 15?

Consider only trips that started on January 15.

```
SELECT
	COUNT(*)
FROM yellow_taxi_data
WHERE
	1 = 1
	AND tpep_pickup_datetime::DATE = '2021-01-15'
;
```

There were 53,024 trips on January 15.

## Question 4. Largest tip for each day

Find the largest tip for each day. 
On which day it was the largest tip in January?

Use the pick up time for your calculations.

(note: it's not a typo, it's "tip", not "trip")

```
SELECT
	tpep_pickup_datetime::DATE
	, MAX(tip_amount) "max_tip_amount"
FROM yellow_taxi_data
WHERE
	1 = 1
GROUP BY
	tpep_pickup_datetime::DATE
ORDER BY
	MAX(tip_amount) DESC
;
```

The largest tip of $1140.44 was on January 20.

```
"2021-01-20"	1140.44
"2021-01-04"	696.48
"2021-01-03"	369.4
"2021-01-26"	250
"2021-01-09"	230
"2021-01-19"	200.8
"2021-01-30"	199.12
"2021-01-12"	192.61
"2021-01-21"	166
"2021-01-01"	158
"2021-01-05"	151
"2021-01-11"	145
"2021-01-24"	122
"2021-01-02"	109.15
"2021-01-31"	108.5
"2021-01-25"	100.16
"2021-01-16"	100
"2021-01-27"	100
"2021-01-06"	100
"2021-01-08"	100
"2021-01-23"	100
"2021-01-13"	100
"2021-01-15"	99
"2021-01-07"	95
"2021-01-14"	95
"2021-01-22"	92.55
"2021-01-10"	91
"2021-01-18"	90
"2021-01-28"	77.14
"2021-01-29"	75
"2021-01-17"	65
"2020-12-31"	4.08
"2021-02-22"	1.76
"2021-02-01"	1.54
"2008-12-31"	0
"2009-01-01"	0
```

## Question 5. Most popular destination

What was the most popular destination for passengers picked up 
in central park on January 14?

Use the pick up time for your calculations.

Enter the zone name (not id). If the zone name is unknown (missing), write "Unknown" 

```
SELECT
	zones_dropoff."Zone"
	, COUNT(*)
FROM yellow_taxi_data taxi
LEFT JOIN zones zones_pickup
ON taxi."PULocationID" = zones_pickup."LocationID"
LEFT JOIN zones zones_dropoff
ON taxi."DOLocationID" = zones_dropoff."LocationID"
WHERE
	1 = 1
	AND taxi.tpep_pickup_datetime::DATE = '2021-01-14'
	AND zones_pickup."Zone" = 'Central Park'
GROUP BY
	zones_dropoff."Zone"
ORDER BY 
	COUNT(*) DESC
;
```

The most popular destination was the Upper East Side North for passengers starting in Central Park on January 14, 2021.

```
"Upper East Side South"	97
"Upper East Side North"	94
"Lincoln Square East"	83
"Upper West Side North"	68
"Upper West Side South"	60
"Central Park"	59
"Midtown Center"	56
"Yorkville West"	40
"Lenox Hill West"	39
"Lincoln Square West"	36
"Midtown North"	30
"Yorkville East"	25
"Manhattan Valley"	24
"Midtown East"	23
"East Harlem South"	22
"Lenox Hill East"	21
"Murray Hill"	20
"Midtown South"	19
"Clinton East"	19
"Garment District"	18
"Union Sq"	15
"West Chelsea/Hudson Yards"	13
"Central Harlem"	13
"UN/Turtle Bay South"	12
"Sutton Place/Turtle Bay North"	12
"Little Italy/NoLiTa"	11
"Morningside Heights"	11
"Clinton West"	10
"Greenwich Village North"	9
"Times Sq/Theatre District"	9
"West Village"	8
"East Harlem North"	8
"Washington Heights South"	7
"East Chelsea"	7
"Gramercy"	6
"Hamilton Heights"	5
"Central Harlem North"	5
"Meatpacking/West Village West"	5
"Flatiron"	4
"Bloomingdale"	4
"East Village"	4
"Steinway"	3
"TriBeCa/Civic Center"	3
"NV"	3
"Washington Heights North"	3
"Manhattanville"	2
"Financial District North"	2
"Greenwich Village South"	2
"Hudson Sq"	2
"Kips Bay"	2
"Long Island City/Hunters Point"	2
"Lower East Side"	2
"Battery Park City"	2
"Penn Station/Madison Sq West"	2
"SoHo"	2
"Stuy Town/Peter Cooper Village"	2
"Sunset Park West"	2
"Boerum Hill"	1
"Sunnyside"	1
"Bay Ridge"	1
"Pelham Bay"	1
"Park Slope"	1
"Old Astoria"	1
"Ocean Hill"	1
"Morrisania/Melrose"	1
"Jackson Heights"	1
"Inwood"	1
"Flatlands"	1
"Flatbush/Ditmas Park"	1
"East Williamsburg"	1
"East Flatbush/Farragut"	1
"Eastchester"	1
"Crown Heights South"	1
"Williamsbridge/Olinville"	1
"Windsor Terrace"	1
"Spuyten Duyvil/Kingsbridge"	1
"Seaport"	1
```

## Question 6. Most expensive locations

What's the pickup-dropoff pair with the largest 
average price for a ride (calculated based on `total_amount`)?

Enter two zone names separated by a slash

For example:

"Jamaica Bay / Clinton East"

If any of the zone names are unknown (missing), write "Unknown". For example, "Unknown / Clinton East". 

```
SELECT
	CONCAT(
		(
			CASE
			WHEN zones_pickup."Zone" IS NULL
			THEN 'Unknown'
			ELSE zones_pickup."Zone"
			END
		 )
		, ' / '
		, (
			CASE
			WHEN zones_dropoff."Zone" IS NULL
			THEN 'Unknown'
			ELSE zones_dropoff."Zone"
			END
		   )
	) "Origin / Destination"
	, AVG(total_amount)
FROM yellow_taxi_data taxi
LEFT JOIN zones zones_pickup
ON taxi."PULocationID" = zones_pickup."LocationID"
LEFT JOIN zones zones_dropoff
ON taxi."DOLocationID" = zones_dropoff."LocationID"
WHERE
	1 = 1
GROUP BY
	"Origin / Destination"
ORDER BY 
	AVG(total_amount) DESC
;
```

On average, the most expensive trip was from Alphabet City to an unknown destination.  Otherwise, the most expensive trip was from Union Square to Canarsie and cost $262.85 on average.

```
"Alphabet City / Unknown"	2292.4
"Union Sq / Canarsie"	262.852
"Ocean Hill / Unknown"	234.51
"Long Island City/Hunters Point / Clinton East"	207.61
"Boerum Hill / Woodside"	200.3
"Baisley Park / Unknown"	181.4425
"Bushwick South / Long Island City/Hunters Point"	156.96
"Willets Point / Unknown"	154.42
"Co-Op City / Dyker Heights"	151.37
"Rossville/Woodrow / Pelham Bay Park"	151
...
```

## Submitting the solutions

* Form for submitting: https://forms.gle/yGQrkgRdVbiFs8Vd7
* You can submit your homework multiple times. In this case, only the last submission will be used. 

Deadline: 26 January (Wednesday), 22:00 CET


## Solution

Here is the solution to questions 3-6: [video](https://www.youtube.com/watch?v=HxHqH2ARfxM&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb)

