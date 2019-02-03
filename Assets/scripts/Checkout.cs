using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using TMPro;
using System.IO;

public class Checkout : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        UpdateText();
    }

    // Update is called once per frame
    void Update()
    {

    }

    void UpdateText()
    {
        int id = this.transform.parent.GetComponent<cartId>().cId;
        HttpWebRequest request = (HttpWebRequest)WebRequest.Create("http://480b2321.ngrok.io/carts/" + id);
        request.Method = "GET";

        HttpWebResponse response = (HttpWebResponse)request.GetResponse();
        StreamReader reader = new StreamReader(response.GetResponseStream());
        string jsonResponse = reader.ReadToEnd();
        this.transform.GetComponent<TextMeshProUGUI>().text = jsonResponse;

    }

    void CompleteCheckout() 
    {
        HttpWebRequest request = (HttpWebRequest)WebRequest.Create("http://480b2321.ngrok.io/carts/1/checkout");
        request.Method = "POST";
        request.ContentType = "application/json";

        using (var streamWriter = new StreamWriter(request.GetRequestStream()))
        {
            string json = "{\"user_id\":\"1\"}";

            streamWriter.Write(json);
            streamWriter.Flush();
            streamWriter.Close();
        }

        HttpWebResponse response = (HttpWebResponse)request.GetResponse();
        StreamReader reader = new StreamReader(response.GetResponseStream());
        string jsonResponse = reader.ReadToEnd();
        this.transform.GetComponent<TextMeshProUGUI>().text = jsonResponse;

    }
}
