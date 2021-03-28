<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<%@ taglib uri="http://tiles.apache.org/tags-tiles"  prefix="tiles"%>

<!DOCTYPE html>
<html lang="kor">
	<head>
		<tiles:insertAttribute name="head" />
	</head>
	
	<body>
		<tiles:insertAttribute name="header" />
		<tiles:insertAttribute name="center" />
	    <tiles:insertAttribute name="footer" />
	</body>
</html>