<?xml version="1.0" encoding="ISO-8859-1"?>

<!-- Exemplo de sincronismo sem a interacao do usuario e com reuso apenas de relacoes-->
<ncl id="syncEx" xmlns="http://www.ncl.org.br/NCL3.0/EDTVProfile">
	<head>
		<ruleBase>
		</ruleBase>
		<regionBase>
			
			
					<region height="50%" id="video" left="25%" top="25%" width="25%" zIndex="3" />
					<region height="50%" id="slides" left="50%" top="25%" width="50%" zIndex="3" />
					
		
		</regionBase>

		<descriptorBase>
			<descriptor id="main_video" region="video"/>
			<descriptor id="bkg" region="backgrounReg"/>
			<descriptor id="slide" region="slides"/>

			
		</descriptorBase>

		<connectorBase>

			<causalConnector id="onBeginStart">
				<simpleCondition role="onBegin"/>
				<simpleAction role="start" max="unbounded" qualifier="par"/>
			</causalConnector>
			<causalConnector id="onBeginEnd">
				<simpleCondition role="onBegin"/>
				<simpleAction role="end" max="unbounded" qualifier="par"/>
			</causalConnector>
			<causalConnector id="onSelectionStopStart">
				<simpleCondition role="onSelection"/>
				<compoundAction operator="seq">
					<simpleAction role="stop" max="unbounded" qualifier="par"/>
					<simpleAction role="start" max="unbounded" qualifier="par"/>					
				</compoundAction>	
			</causalConnector>
		<causalConnector id="onEndStop">
				<simpleCondition role="onEnd"/>

				<simpleAction role="stop" max="unbounded"/>


			</causalConnector>
		</connectorBase>
	</head>

	<body>




	</body>
</ncl>
