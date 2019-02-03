using System.Collections;
using System.Net;
using System;
using System.IO;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class AddtoCart : MonoBehaviour
{
    public TextMeshProUGUI infoText;
    // Start is called before the first frame update
    void Start()
    {
      
    }

   public void UpdateText()
    {
        HttpWebRequest request = (HttpWebRequest)WebRequest.Create("http://178.128.229.75:5000/carts/1");
        request.Method = "PUT";
        request.ContentType = "application/json";

        using (var streamWriter = new StreamWriter(request.GetRequestStream()))
        {
            string json = "{\"product_id\":\"1\"}";

            streamWriter.Write(json);
            streamWriter.Flush();
            streamWriter.Close();
        }

        HttpWebResponse response = (HttpWebResponse)request.GetResponse();
        StreamReader reader = new StreamReader(response.GetResponseStream());
        string jsonResponse = reader.ReadToEnd();
        infoText.text = jsonResponse;
    }
    // Update is called once per frame
    void Update()
    {
        
    }
}