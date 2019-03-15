using System.Collections;
using System.Net;
using System;
using System.IO;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using System.Collections;

public class RemovefromCart : MonoBehaviour
{

// Start is called before the first frame update
void Start()
    { 

    }

    public void UpdateText()
    {
        int id = this.transform.parent.parent.parent.GetComponent<productId>().pId;
        HttpWebRequest request = (HttpWebRequest)WebRequest.Create("http://dc3e9063.ngrok.io/carts/5");
        request.Method = "DELETE";
        request.ContentType = "application/json";


        using (var streamWriter = new StreamWriter(request.GetRequestStream()))
        {
            string json = "{\"product_id\":\"" + id + "\"}";

            streamWriter.Write(json);
            streamWriter.Flush();
            streamWriter.Close();
        }

        HttpWebResponse response = (HttpWebResponse)request.GetResponse();
        StreamReader reader = new StreamReader(response.GetResponseStream());
        string jsonResponse = reader.ReadToEnd();
        jsonResponse.Replace("\"", "");
        StartCoroutine(UpdatePopUp(jsonResponse));
    }

    IEnumerator UpdatePopUp(string jsonResponse)
    {

        this.transform.GetComponent<TextMeshProUGUI>().text = jsonResponse;
        yield return new WaitForSeconds(5);
        this.transform.GetComponent<TextMeshProUGUI>().text = "";
    }
    // Update is called once per frame
    void Update()
    {
        
    }
}
