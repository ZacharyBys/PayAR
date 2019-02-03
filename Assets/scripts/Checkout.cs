using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using TMPro;
using System.IO;
using Vuforia;

public class Checkout : VuforiaMonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        UpdateText();
    }

    // Update is called once per frame
    void Update()
    {
       if (this.transform.parent.parent.parent.parent.GetComponent<TrackableBehaviour>().CurrentStatus == TrackableBehaviour.Status.DETECTED)
        {
            UpdateText();
        }
    }

    public void UpdateText()
    {

        //int id = this.transform.parent.parent.parent.parent.GetComponent<cartId>().cId;
        HttpWebRequest request = (HttpWebRequest)WebRequest.Create("http://480b2321.ngrok.io/carts/5");
        request.Method = "GET";

        HttpWebResponse response = (HttpWebResponse)request.GetResponse();
        StreamReader reader = new StreamReader(response.GetResponseStream());
        string jsonResponse = reader.ReadToEnd();

        //jsonRes
        this.transform.GetComponent<TextMeshProUGUI>().text = jsonResponse;

    }

    public void CompleteCheckout() 
    {
        //int id = this.transform.parent.parent.parent.parent.GetComponent<cartId>().cId;
        int id = 5;
        HttpWebRequest request = (HttpWebRequest)WebRequest.Create("http://480b2321.ngrok.io/carts/"+id+"/checkout");
        request.Method = "POST";

        HttpWebResponse response = (HttpWebResponse)request.GetResponse();
        StreamReader reader = new StreamReader(response.GetResponseStream());
        string jsonResponse = reader.ReadToEnd();
        this.transform.GetComponent<TextMeshProUGUI>().text = jsonResponse;

    }
}
