/* Teachers need to create a forum activity with name=nocopy ; this will fill this report, which will be used by the script 
to isolate courses which will be copied without any ressource  */

SELECT 
	c.id,
	c.category "categoryid",
	c.fullname "course fullname", 
	cat.name "category",
	fm.name
	/* ccc.name "parent category 2", */
	/* cccc.name "parent category 3", */
	/* ccccc.name "parent category 4",*/

FROM prefix_forum fm

JOIN prefix_course c ON c.id = fm.course
JOIN prefix_course_categories cat ON cat.id = c.category

WHERE fm.name = "nocopy"
