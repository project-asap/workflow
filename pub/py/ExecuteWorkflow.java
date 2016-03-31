import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URLEncoder;

import javax.xml.bind.JAXB;
import javax.xml.bind.JAXBContext;
import javax.xml.bind.Marshaller;

import gr.ntua.cslab.asap.client.ClientConfiguration;
import gr.ntua.cslab.asap.client.OperatorClient;
import gr.ntua.cslab.asap.client.RestClient;
import gr.ntua.cslab.asap.client.WorkflowClient;
import gr.ntua.cslab.asap.operators.AbstractOperator;
import gr.ntua.cslab.asap.operators.Dataset;
import gr.ntua.cslab.asap.operators.NodeName;
import gr.ntua.cslab.asap.operators.Operator;
import gr.ntua.cslab.asap.rest.beans.OperatorDictionary;
import gr.ntua.cslab.asap.rest.beans.WorkflowDictionary;
import gr.ntua.cslab.asap.workflow.AbstractWorkflow1;
import gr.ntua.cslab.asap.workflow.WorkflowNode;
import gr.ntua.cslab.asap.staticLibraries.MaterializedWorkflowLibrary;

public class ExecuteWorkflow {
	public static void main(String[] args) throws Exception {

		ClientConfiguration conf = new ClientConfiguration("hdp1.itc.unipi.it", 1323);
		WorkflowClient cli = new WorkflowClient();
		cli.setConfiguration(conf);

        String name = args[0];
        String directory = args[1];
		AbstractWorkflow1 abstractWorkflow = new AbstractWorkflow1(name);

		abstractWorkflow.readFromDir(directory);

		cli.addAbstractWorkflow(abstractWorkflow);

		String policy ="metrics,cost,execTime\n"+
						"groupInputs,execTime,max\n"+
						"groupInputs,cost,sum\n"+
						"function,2*execTime+3*cost,min";

		String materializedWorkflow = cli.materializeWorkflow(name, policy);
		System.out.println(materializedWorkflow);

		WorkflowDictionary wd = cli.getMaterializedWorkflowDescription(name);
		for(OperatorDictionary op : wd.getOperators()){
			if(op.getIsOperator().equals("true"))
				System.out.println(op.getNameNoID()+" "+op.getCost());
		}
		
        cli.executeWorkflow(materializedWorkflow);
	}
}