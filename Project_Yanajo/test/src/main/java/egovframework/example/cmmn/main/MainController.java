package egovframework.example.cmmn.main;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class MainController {

	@RequestMapping(value = "/mainInit.do")
	public String mainInit() {		
		
		return "main-tiles";
	}
}