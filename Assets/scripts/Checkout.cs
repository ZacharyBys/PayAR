using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using TMPro;
using System.IO;
using Vuforia;
using System;

public class Checkout : VuforiaMonoBehaviour
{
    string items;
    float total;
    // Start is called before the first frame update
    void Start()
    {
    }
    void Update() {
        if (Input.GetKeyDown("space"))
        {
            UpdateText();
        }
    }

  //{"cart": {"id": "5", "items": [{"product": {"id": 1, "name": "CSE Mints", "price": 3.99, "inventory_count": 67, "description": "Peppermint"}, "quantity": 1}, 
  //{"product": {"id": 3, "name": "MLH Hardware Sticker", "price": 10.99, "inventory_count": 18, "description": "Presented by Digi-Key"}, "quantity": 2}], "total": 25.97}}

          
        public void UpdateText() { 
        //int id = this.transform.parent.parent.parent.parent.GetComponent<cartId>().cId;
        HttpWebRequest request = (HttpWebRequest)WebRequest.Create("http://dc3e9063.ngrok.io/carts/5");
        request.Method = "GET";

        HttpWebResponse response = (HttpWebResponse)request.GetResponse();
        StreamReader reader = new StreamReader(response.GetResponseStream());
        string jsonResponse = reader.ReadToEnd();
        //Debug.Log(jsonResponse);
        //string[] items = jsonResponse.Split(new string[] { "\"name\": \"" }, StringSplitOptions.None);
        //string names = "";
        //for(int i=1;i<items.Length;i+=2)
        //{
        //    names += items[i].Split('"')[0];
        //}
        //jsonResponse.Split(new string[] { "\"total\": \"" }, StringSplitOptions.None);
        jsonResponse = jsonResponse.Replace("\\n", "\n");
        jsonResponse = jsonResponse.Replace("\\t", "\t");
        this.transform.GetComponent<TextMeshProUGUI>().text = jsonResponse;
        
        //this.transform.GetComponent<TextMeshProUGUI>().text += "total:" + total;

    }


    public void CompleteCheckout() 
    {
        //int id = this.transform.parent.parent.parent.parent.GetComponent<cartId>().cId;
        int id = 5;
        HttpWebRequest request = (HttpWebRequest)WebRequest.Create("http://dc3e9063.ngrok.io/carts/" + id+"/checkout");
        request.Method = "POST";

        HttpWebResponse response = (HttpWebResponse)request.GetResponse();
        StreamReader reader = new StreamReader(response.GetResponseStream());
        string jsonResponse = reader.ReadToEnd();
        this.transform.GetComponent<TextMeshProUGUI>().text = jsonResponse;

    }
}
